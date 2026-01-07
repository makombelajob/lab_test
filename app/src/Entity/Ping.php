<?php

namespace App\Entity;

use App\Repository\PingRepository;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: PingRepository::class)]
class Ping
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 100, nullable: true)]
    private ?string $hostname = null;

    #[ORM\Column(length: 20, nullable: true)]
    private ?string $ipAddress = null;

    #[ORM\Column(nullable: true)]
    private ?bool $status = null;

    #[ORM\Column(options: ["default" => "CURRENT_TIMESTAMP"])]
    private ?\DateTimeImmutable $scanAt = null;

    #[ORM\ManyToOne(inversedBy: 'ping')]
    private ?User $user = null;

    public function __construct()
    {
        $this->scanAt = new \DateTimeImmutable();
    }
    public function getId(): ?int
    {
        return $this->id;
    }

    public function getHostname(): ?string
    {
        return $this->hostname;
    }

    public function setHostname(?string $hostname): static
    {
        $this->hostname = $hostname;

        return $this;
    }

    public function getIpAddress(): ?string
    {
        return $this->ipAddress;
    }

    public function setIpAddress(?string $ipAddress): static
    {
        $this->ipAddress = $ipAddress;

        return $this;
    }

    public function isStatus(): ?bool
    {
        return $this->status;
    }

    public function setStatus(?bool $status): static
    {
        $this->status = $status;

        return $this;
    }

    public function getScanAt(): ?\DateTimeImmutable
    {
        return $this->scantAt;
    }

    public function setScanAt(\DateTimeImmutable $scantAt): static
    {
        $this->scantAt = $scantAt;

        return $this;
    }

    public function getUser(): ?User
    {
        return $this->user;
    }

    public function setUser(?User $user): static
    {
        $this->user = $user;

        return $this;
    }
}
