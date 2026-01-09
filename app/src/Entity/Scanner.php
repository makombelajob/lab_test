<?php

namespace App\Entity;

use App\Repository\ScannerRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: ScannerRepository::class)]
class Scanner
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column]
    private ?int $port = null;

    #[ORM\Column(length: 50)]
    private ?string $service = null;

    #[ORM\Column(length: 50, nullable: true)]
    private ?string $version = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $scriptVuln = null;

    #[ORM\Column(length: 7)]
    private ?string $state = null;

    #[ORM\Column(length: 30, nullable: true)]
    private ?string $osDetected = null;

    #[ORM\ManyToOne(inversedBy: 'scanner')]
    private ?Ping $ping = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getPort(): ?int
    {
        return $this->port;
    }

    public function setPort(int $port): static
    {
        $this->port = $port;

        return $this;
    }

    public function getService(): ?string
    {
        return $this->service;
    }

    public function setService(string $service): static
    {
        $this->service = $service;

        return $this;
    }

    public function getVersion(): ?string
    {
        return $this->version;
    }

    public function setVersion(?string $version): static
    {
        $this->version = $version;

        return $this;
    }

    public function getScriptVuln(): ?string
    {
        return $this->scriptVuln;
    }

    public function setScriptVuln(?string $scriptVuln): static
    {
        $this->scriptVuln = $scriptVuln;

        return $this;
    }

    public function getState(): ?string
    {
        return $this->state;
    }

    public function setState(string $state): static
    {
        $this->state = $state;

        return $this;
    }

    public function getOsDetected(): ?string
    {
        return $this->osDetected;
    }

    public function setOsDetected(?string $osDetected): static
    {
        $this->osDetected = $osDetected;

        return $this;
    }

    public function getPing(): ?Ping
    {
        return $this->ping;
    }

    public function setPing(?Ping $ping): static
    {
        $this->ping = $ping;

        return $this;
    }
}
